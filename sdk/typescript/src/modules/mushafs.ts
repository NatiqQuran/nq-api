import * as MushafsType from "../types/mushafs";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class MushafsImport extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /mushafs/import/ */
    async mushafs_import_create(config?: RequestConfig
    ): Promise<AxiosResponse<MushafsType.MushafsImportPostResponseData>> {
        return await this.axiosPost(`/mushafs/import/`, config);
    }
}

export class MushafsController extends BaseController {
    public readonly import: MushafsImport;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.import = new MushafsImport(this.conn);
    }
    
    /** GET /mushafs/ */
    async list(config?: RequestConfig<MushafsType.MushafsListRequestParams>
    ): Promise<AxiosResponse<MushafsType.MushafsListResponseData>> {
        return await this.axiosGet(`/mushafs/`, config);
    }
    
    /** POST /mushafs/ */
    async create(data: MushafsType.MushafsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<MushafsType.MushafsCreateResponseData>> {
        return await this.axiosPost(`/mushafs/`, data, config);
    }
    
    /** GET /mushafs/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<MushafsType.MushafsRetrieveResponseData>> {
        return await this.axiosGet(`/mushafs/${uuid}/`, config);
    }
    
    /** PUT /mushafs/{uuid}/ */
    async update(uuid: string, data: MushafsType.MushafsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<MushafsType.MushafsUpdateResponseData>> {
        return await this.axiosPut(`/mushafs/${uuid}/`, data, config);
    }
    
    /** PATCH /mushafs/{uuid}/ */
    async partialUpdate(uuid: string, data: MushafsType.MushafsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<MushafsType.MushafsPartialupdateResponseData>> {
        return await this.axiosPatch(`/mushafs/${uuid}/`, data, config);
    }
    
    /** DELETE /mushafs/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/mushafs/${uuid}/`, config);
    }
    
}